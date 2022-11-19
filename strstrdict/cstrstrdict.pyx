# cython: language_level=3, c_string_type=unicode, c_string_encoding=utf8
# distutils: language=c++

from cython.operator cimport preincrement, dereference  # noqa
from libc.stdint cimport uint64_t
from libcpp.unordered_map cimport unordered_map  # noqa
from libcpp.string cimport string

from strstrdict.parallel_hashmap cimport flat_hash_map, btree_map  # noqa
from strstrdict.cramped_string cimport cramped_string  # noqa


cdef cramped_string cramped(s: str):
    return <cramped_string><string>s


cdef class CStrStrDict:

    cdef flat_hash_map[cramped_string,cramped_string] umap
    cdef uint64_t modcount

    def __cinit__(self):
        self.modcount = 0

    def __getitem__(self, key: str) -> str:
        it = self.umap.find(cramped(key))
        if it == self.umap.end():
            raise KeyError(key)
        return <string>dereference(it).second

    def __setitem__(self, key: str, value: str):
        self.modcount += 1
        self.umap[cramped(key)] = cramped(value)

    def __delitem__(self, key: str):
        self.modcount += 1
        if not self.umap.erase(cramped(key)):
            raise KeyError(key)

    def __len__(self):
        return self.umap.size()

    def __iter__(self):
        start_modcount = self.modcount
        for it in self.umap:
            if start_modcount != self.modcount:
                raise RuntimeError("dictionary changed size or contents during iteration")
            yield <string>it.first
