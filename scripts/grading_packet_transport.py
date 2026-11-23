"""Unwrap only known lossless grader encoding before a second compaction stage."""
from round25_grader_pool import decode
LEGACY='p indexes verbatim_pool; join concatenates literals and slice [pool-index,start,end] of prior strings (end exclusive).'
def unpool_for_refit(value):
 d=value.get('delivered',{})
 if d.get('pool_encoding')==LEGACY and isinstance(d.get('verbatim_pool'),list):
  # The old packet already proves its round trip at construction. Decode its
  # transport references rather than overwrite its pool with a second pool.
  return decode(value)
 return value
