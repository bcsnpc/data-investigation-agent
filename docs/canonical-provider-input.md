# Canonical provider request input

Equivalent nested dictionaries now serialize with sorted JSON keys at the
provider boundary. Catalog reconstruction may change insertion order, so an
unsorted input string made strict replay depend on local construction order.
The synthetic SDK test reverses nested insertion order and requires identical
request bytes, the same parsed payload and unchanged character count.

This applies to future requests only. Old sealed bodies are not rewritten;
strict matching is not relaxed. The Round Five EMPTY and 16 offline attempts
retain their differing results. No live replacement attempt or credit is used.
Golden directory coverage is unchanged: two entries, one SQL object, 7,540
payload characters before and after; sorting adds no fields or text. Engine
bytes changed, invalidating prior freezes. This is not evidence that the old
fifteen-ticket acceptance gate passes.

CI exposed the intake-family test's current synthetic projection still expecting
the old unsorted wire string. Its current-request expectation now sorts keys too;
the immutable source fixture and original responses remain unchanged. All twelve
synthetic family cases must still reproduce their original interpreted decisions.
