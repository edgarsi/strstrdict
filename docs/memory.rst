Memory Use Details
------------------

Strings are stored as their size and contents, no trailing '\\0'. String sizes
are stored as the minimum bytes necessary to represent them, plus an extra byte.
So, for strings less than 256 bytes long, the string header takes 2 bytes.

The string size and contents are stored using ``PyMem_Malloc``, which has a max
7 byte overhead. `[1]`_

The pointers to the allocated memory are stored in
`parallel_hashmap`_::flat_hash_map, which uses up to 2x memory overhead.

For example, representing a string of length 10 requires 10+2 bytes, which are
stored in 16 bytes, plus an 8 byte pointer stored in the hash map. This pointer
may contribute up to 16 bytes in the hash map, let's use the average of 12
bytes. So, the total memory use is 16+12=28 bytes.

An alternative store is ``parallel_hashmap::btree_map``, using which saves 20%
memory, when working short strings. However, it is 3 times slower. The trade-off
does not seem worth it.

.. _[1]: https://rushter.com/blog/python-memory-managment/
.. _parallel_hashmap: https://github.com/greg7mdp/parallel-hashmap
