"""Bounded-memory exact tape JSON. Existing canonical bytes and seals are unchanged."""
import hashlib
import json
from pathlib import Path
from collections.abc import Sequence

CHUNK=1024*1024


class DiskEvents(Sequence):
    """Only offsets are resident; each access reads one original event."""
    def __init__(self,path,offsets=None):
        self.path=Path(path);self.offsets=[] if offsets is None else offsets
    def __len__(self):return len(self.offsets)
    def __getitem__(self,index):
        if isinstance(index,slice):return (self[i] for i in range(*index.indices(len(self))))
        offset,size=self.offsets[index]
        with self.path.open('rb') as source:
            source.seek(offset);return json.loads(source.read(size))
    def append(self,event):
        raw=json.dumps(event,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
        with self.path.open('ab') as target:
            offset=target.tell();target.write(raw+b'\n');target.flush()
        self.offsets.append((offset,len(raw)))


def chunks(value):
    """Canonical JSON, streaming the event array rather than copying its bodies."""
    if isinstance(value,dict):
        yield b'{'
        for i,key in enumerate(sorted(value)):
            if i:yield b','
            yield from chunks(key);yield b':';yield from chunks(value[key])
        yield b'}'
    elif isinstance(value,Sequence) and not isinstance(value,(str,bytes,bytearray)):
        yield b'['
        for i,item in enumerate(value):
            if i:yield b','
            yield from chunks(item)
        yield b']'
    else:
        for text in json.JSONEncoder(ensure_ascii=False,sort_keys=True,separators=(',',':')).iterencode(value):
            for offset in range(0,len(text),CHUNK):yield text[offset:offset+CHUNK].encode()


def digest(value):
    result=hashlib.sha256()
    for chunk in chunks(value):result.update(chunk)
    return result.hexdigest()


class Reader:
    """A JSON value at a time, with byte positions into the original file."""
    def __init__(self,stream):self.stream=stream;self.buffer=b'';self.offset=0;self.decoder=json.JSONDecoder()
    def fill(self):
        data=self.stream.read(CHUNK)
        if not data:raise ValueError('TAPE_TRUNCATED_JSON')
        self.buffer+=data
    def consume(self,count):self.buffer=self.buffer[count:];self.offset+=count
    def whitespace(self):
        while True:
            if not self.buffer:
                data=self.stream.read(CHUNK)
                if not data:return
                self.buffer=data
            count=len(self.buffer)-len(self.buffer.lstrip())
            if not count:return
            self.consume(count)
    def token(self,expected):
        self.whitespace()
        while not self.buffer:self.fill()
        if not self.buffer.startswith(expected):raise ValueError('TAPE_JSON_DELIMITER')
        self.consume(len(expected))
    def value(self):
        self.whitespace();start=self.offset
        while True:
            try:
                text=self.buffer.decode('utf8');value,end=self.decoder.raw_decode(text)
                # A scalar number can continue into the next buffer.
                if end==len(text):self.fill();continue
                size=len(text[:end].encode());self.consume(size);return value,start,size
            except (UnicodeDecodeError,json.JSONDecodeError):self.fill()


def load(path):
    """Read metadata and index events without materializing the capture."""
    path=Path(path);value={}
    with path.open('rb') as stream:
        reader=Reader(stream);reader.token(b'{')
        while True:
            key,_,_=reader.value()
            if not isinstance(key,str) or key in value:raise ValueError('TAPE_JSON_DUPLICATE_OR_INVALID_KEY')
            reader.token(b':')
            if key=='events':
                reader.token(b'[');events=DiskEvents(path);reader.whitespace()
                if not reader.buffer.startswith(b']'):
                    while True:
                        _,offset,size=reader.value();events.offsets.append((offset,size));reader.whitespace()
                        if reader.buffer.startswith(b']'):break
                        reader.token(b',')
                reader.token(b']');value[key]=events
            else:value[key]=reader.value()[0]
            reader.whitespace()
            if reader.buffer.startswith(b'}'):break
            reader.token(b',')
        reader.token(b'}');reader.whitespace()
        if reader.buffer or stream.read(1):raise ValueError('TAPE_JSON_TRAILING_CONTENT')
    return value
