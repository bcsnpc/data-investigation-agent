# Canonical provider tape matching

Provider request/response candidates compare byte-exactly after parsing JSON,
sorting object keys and serializing without whitespace. The declared request
input JSON string, response base64 JSON carrier and function-call arguments JSON
are canonicalized as structured content. Ordinary prose, query text and array
order remain content. Duplicate keys, non-finite numbers and invalid JSON refuse.
Physical requests remain byte-exact. Original sealed bytes are never rewritten.
The same transport consumer is applied to archived producer revisions.

Eight provider tests cover formatting equality, one-field differences, literal
prose/array changes, nested carriers, malformed JSON and historical/current
consumers. Five budget tests remain green. This adds no planner context content;
initial directory and wire coverage are unchanged. No live run or estate read in
this implementation. Prior freezes invalidated. Fifteen-tape regrading follows.
