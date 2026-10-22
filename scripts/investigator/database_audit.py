"""Bounded complete JSON-value batches; caller owns exact normalization."""


class CompleteValues:
    def __init__(self, safe, limit=256*1024):
        if type(limit) is not int or limit<2:
            raise ValueError('AUDIT_BATCH_BOUND_REQUIRED')
        self.safe,self.limit=safe,limit
        self.values=[]
        self.size=2

    def flush(self):
        if self.values:
            self.safe(b'['+b','.join(self.values)+b']')
            self.values.clear()
            self.size=2

    def add(self, raw):
        if len(raw)+2>self.limit:
            self.flush()
            self.safe(raw)
            return
        if self.size+len(raw)+(1 if self.values else 0)>self.limit:
            self.flush()
        self.size+=len(raw)+(1 if self.values else 0)
        self.values.append(raw)

    def individual(self, raw):
        self.flush()
        self.safe(raw)
