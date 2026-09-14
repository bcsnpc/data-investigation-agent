"""Finite local worker session; only approved queued tickets can execute."""
from threading import Event, Lock, Thread
import time
from ticket_worker import process_one


class BackgroundWorker:
    def __init__(self,store,config,estate_loader,max_jobs=1,max_seconds=900,poll_seconds=5,process=process_one):
        if isinstance(max_jobs,bool) or not isinstance(max_jobs,int) or not 1<=max_jobs<=10:
            raise ValueError('Worker job limit must be 1 to 10')
        if not 1<=max_seconds<=3600 or not 0.01<=poll_seconds<=60:
            raise ValueError('Invalid worker duration or polling interval')
        self.store=store;self.config=config;self.estate_loader=estate_loader;self.process=process
        self.max_jobs=max_jobs;self.max_seconds=max_seconds;self.poll_seconds=poll_seconds
        self.stop_event=Event();self.lock=Lock();self.thread=None
        self.state={'status':'NOT_STARTED','processed':0,'max_jobs':max_jobs,'max_seconds':max_seconds}

    def status(self):
        with self.lock:return dict(self.state)

    def update(self,**values):
        with self.lock:self.state.update(values)

    def start(self):
        if self.thread is not None:raise RuntimeError('Worker session already started')
        self.thread=Thread(target=self.run,name='investigation-worker',daemon=False)
        self.thread.start()

    def stop(self):
        self.stop_event.set()
        if self.thread is not None:self.thread.join()

    def run(self):
        deadline=time.monotonic()+self.max_seconds;count=0
        self.update(status='RUNNING')
        try:
            while not self.stop_event.is_set() and count<self.max_jobs and time.monotonic()<deadline:
                # Reload current lineage configuration for each claim.
                result=self.process(self.store,self.config,self.estate_loader(),approved_only=True)
                if result['status']!='IDLE':
                    count+=1;self.update(processed=count,last_result=result)
                else:self.stop_event.wait(min(self.poll_seconds,max(0,deadline-time.monotonic())))
            reason='STOPPED' if self.stop_event.is_set() else ('JOB_LIMIT' if count>=self.max_jobs else 'TIME_LIMIT')
            self.update(status=reason)
        except Exception as exc:
            # Do not retry uncertain work or expose provider/connection messages.
            self.update(status='FAILED',error_type=type(exc).__name__)
