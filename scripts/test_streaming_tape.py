"""Streaming exact captures must not scale memory with retained tape size."""
import gc
import hashlib
import io
import json
import tempfile
import tracemalloc
import unittest
from pathlib import Path
from unittest.mock import patch
from investigator.process_tape import Tape,bytes_of
from investigator.streaming_tape import DiskEvents,chunks,digest,load
from investigator.atomic_tape_publish import publish_chunks
from test_process_tape import bootstrap


class StreamingTests(unittest.TestCase):
    def test_canonical_stream_preserves_bytes_unicode_and_seal(self):
        value={'version':'v','events':[{'body':'é😀\\\"','n':1.25}], 'exclusions':[]}
        self.assertEqual(b''.join(chunks(value)),bytes_of(value))
        self.assertEqual(digest(value),hashlib.sha256(bytes_of(value)).hexdigest())

    def test_indexed_roundtrip_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary)/'tape.json'
            with patch.dict('os.environ',{'DIA_STREAMING_CAPTURE':'1'}):
                tape=Tape(path,bootstrap())
                self.assertIsInstance(tape.events,DiskEvents)
                tape.event('CONFIGURATION',bytes_of({'text':'é😀'}));tape.finish({'done':True})
            value=load(path)
            self.assertIsInstance(value['events'],DiskEvents)
            self.assertEqual(list(value['events']),json.loads(path.read_bytes())['events'])
            self.assertEqual(value['seal'],digest({k:v for k,v in value.items() if k!='seal'}))
            replay=Tape(path);replay.event('CONFIGURATION',bytes_of({'text':'é😀'}));replay.finish({'done':True})
            before=path.read_bytes()
            # Stream loader refuses truncated or appended data rather than accepting a prefix.
            path.write_bytes(before+b'{}')
            with self.assertRaisesRegex(ValueError,'TRAILING'):load(path)
            path.write_bytes(before[:-2])
            with self.assertRaises(ValueError):load(path)

    def test_trace_summary_uses_same_events_without_copying_all_bodies(self):
        from test_tape_trace import TapeTraceTests
        from investigator.tape_trace import recorded_summary
        from types import SimpleNamespace
        import base64
        events=TapeTraceTests().example()
        result=json.loads(base64.b64decode(events[-1]['body']))['result']
        expected=recorded_summary(SimpleNamespace(events=events[:-1],version='test',engine_revision='abc'),result)
        with tempfile.TemporaryDirectory() as temporary:
            disk=DiskEvents(Path(temporary)/'events.jsonl')
            for event in events[:-1]:disk.append(event)
            actual=recorded_summary(SimpleNamespace(events=disk,version='test',engine_revision='abc'),result)
            self.assertEqual(actual,expected)
            self.assertEqual(len(disk),len(events)-1)

    def test_disk_capture_keeps_prior_event_payloads_off_heap(self):
        with tempfile.TemporaryDirectory() as temporary,patch.dict('os.environ',{'DIA_STREAMING_CAPTURE':'1'}):
            tape=Tape(Path(temporary)/'tape.json',bootstrap())
            payload=bytes_of({'retained':'x'*(1024*1024)})
            gc.collect();tracemalloc.start()
            try:
                for i in range(40):tape.event('CONFIGURATION',payload)
                tape.finish({})
                _,peak=tracemalloc.get_traced_memory()
            finally:tracemalloc.stop()
            self.assertGreater(tape.path.stat().st_size,50*1024*1024)
            self.assertLess(peak,20*1024*1024)
            # Above the real loader's threshold, replay events stay file-backed too.
            replay=Tape(tape.path);self.assertIsInstance(replay.events,DiskEvents)
            for i in range(40):replay.event('CONFIGURATION',payload)
            replay.finish({})

    def test_seals_over_two_gib_stream_with_bounded_heap(self):
        # Actual >2GiB canonical bytes are hashed and passed through the atomic
        # publication writer. A counting sink replaces disk, not the serializer,
        # so CI needs neither 2GiB RAM nor 2GiB scratch. No synthetic byte counts.
        payload='x'*(1024*1024)
        class RepeatedEvents(DiskEvents):
            def __init__(self):pass
            def __len__(self):return 2050
            def __iter__(self):
                for i in range(len(self)):yield {'ordinal':i+1,'body':payload}
        value={'version':'synthetic-large-stream','events':RepeatedEvents(),'exclusions':[]}
        class Sink:
            def __init__(self):self.name='synthetic-stage';self.count=0;self.hash=hashlib.sha256()
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def write(self,data):self.count+=len(data);self.hash.update(data)
            def flush(self):pass
            def fileno(self):return -1
        sink=Sink();gc.collect();tracemalloc.start()
        try:
            value['seal']=digest(value)
            with patch('investigator.atomic_tape_publish.tempfile.NamedTemporaryFile',return_value=sink),patch('investigator.atomic_tape_publish.os.fsync'),patch('investigator.atomic_tape_publish.os.replace'),patch.object(Path,'unlink'):
                publish_chunks(Path('synthetic-tape.json'),chunks(value))
            _,peak=tracemalloc.get_traced_memory()
        finally:tracemalloc.stop()
        self.assertGreater(sink.count,2*1024**3)
        self.assertLess(peak,16*1024*1024)
        self.assertRegex(value['seal'],r'^[0-9a-f]{64}$')

if __name__=='__main__':unittest.main()
