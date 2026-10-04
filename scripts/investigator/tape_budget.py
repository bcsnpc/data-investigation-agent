"""Journal admission and settlement, including refused attempts, in run order."""
from functools import wraps
from .process_tape import event,ACTIVE


def decision(method):
    @wraps(method)
    def run(self,db,session_id,key,*args,**kwargs):
        if ACTIVE.get() is None:return method(self,db,session_id,key,*args,**kwargs)
        def snapshot():
            row=db.execute('SELECT status,reserved,actual FROM adaptive_usage WHERE environment=? AND session_id=? AND reservation_key=?',
                           (self.environment,session_id,key)).fetchone()
            return {'reservation':list(row) if row else None,
                    'usage_rows':db.execute('SELECT count(*) FROM adaptive_usage WHERE environment=?',(self.environment,)).fetchone()[0],
                    'policy':self.policy}
        request={'operation':method.__name__,'session_id':session_id,'key':key,'args':list(args),'kwargs':kwargs}
        event('BUDGET',{'phase':'BEFORE','request':request,'state':snapshot()})
        error=None
        try:return method(self,db,session_id,key,*args,**kwargs)
        except BaseException as exc:
            error=type(exc).__name__
            raise
        finally:event('BUDGET',{'phase':'AFTER','request':request,'state':snapshot(),'error':error})
    return run
