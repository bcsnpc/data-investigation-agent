"""Explicit observed change-history ports; never infer an actor from ownership.

Activity and git readers are trusted gateway-bound callbacks installed by the
deployment, not URLs, paths or commands supplied by a question or model.
"""
from copy import deepcopy
from ..estate_graph_contract import timestamp

SOURCES=frozenset({'ITEM_METADATA','FABRIC_ACTIVITY','GIT'})


def validate(row, subject):
    if (not isinstance(row,dict) or set(row)!={'subject','source','actor','at','reason','provenance'}
            or row['subject']!=subject or row['source'] not in SOURCES
            or row['actor'] is not None and (not isinstance(row['actor'],str) or not row['actor'].strip())
            or row['reason'] is not None and (not isinstance(row['reason'],str) or not row['reason'].strip())
            or not isinstance(row['provenance'],dict) or not row['provenance']):
        raise ValueError('EXPLAIN_HISTORY_OBSERVATION_REQUIRED')
    result=deepcopy(row);result['at']=timestamp(row['at'])
    return result


class HistoryPort:
    def __init__(self, *, activity=None, git=None, metadata=None):
        self.activity,self.git,self.metadata=activity,git,metadata

    def read(self,node):
        rows=[];gaps=[];subject=node['id'];metadata=node['properties'].get('observed_metadata',{})
        if self.metadata is not None:
            observed=self.metadata(node)
            if (not isinstance(observed,dict) or set(observed)!={'observations','coverage_gaps'}
                    or not isinstance(observed['observations'],list) or len(observed['observations'])>100
                    or not isinstance(observed['coverage_gaps'],list) or len(observed['coverage_gaps'])>100
                    or any(row.get('source')!='ITEM_METADATA' for row in observed['observations'])):
                raise ValueError('EXPLAIN_HISTORY_BOUND')
            rows.extend(validate(row,subject) for row in observed['observations'])
            gaps.extend(observed['coverage_gaps'])
        # Native naming belongs only at this platform boundary. A modified item
        # is not automatically a changed formula, a refresh or a causal event.
        at=metadata.get('modified_at') or metadata.get('modifiedDateTime')
        actor=metadata.get('modified_by') or metadata.get('modifiedBy')
        if isinstance(actor,dict):actor=actor.get('displayName') or actor.get('userPrincipalName') or actor.get('id')
        if at:
            proof=metadata.get('provenance')
            if not isinstance(proof,dict) or not proof:
                gaps.append({'source':'ITEM_METADATA','reason':'MODIFIED_METADATA_HAS_NO_OBSERVATION_PROVENANCE'})
            else:
                rows.append(validate({'subject':subject,'source':'ITEM_METADATA','actor':actor,
                                      'at':at,'reason':metadata.get('reason'),'provenance':proof},subject))
        elif self.metadata is None:gaps.append({'source':'ITEM_METADATA','reason':'NO_OBSERVED_MODIFIED_TIME'})
        for source,callback in (('FABRIC_ACTIVITY',self.activity),('GIT',self.git)):
            if callback is None:
                gaps.append({'source':source,'reason':'NO_APPROVED_READER_BINDING'})
                continue
            try:
                observed=callback(subject)
                if not isinstance(observed,list) or len(observed)>100:
                    raise ValueError('EXPLAIN_HISTORY_BOUND')
                if not observed:gaps.append({'source':source,'reason':'NO_EVENTS_RETURNED; not proof no change occurred'})
                for item in observed:
                    if item.get('source')!=source:raise ValueError('EXPLAIN_HISTORY_SOURCE_DIFFERS')
                    rows.append(validate(item,subject))
            except Exception as exc:
                from ..live_gateway import GatewayDenied
                if isinstance(exc,GatewayDenied):raise
                gaps.append({'source':source,'reason':getattr(exc,'safe_reason',type(exc).__name__)})
        return {'observations':sorted(rows,key=lambda r:r['at'],reverse=True),'coverage_gaps':gaps}
