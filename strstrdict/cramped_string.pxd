# cython: language_level=3
# distutils: language=c++
from libcpp.string cimport string


cdef extern from "cramped_string.h":
    cdef cppclass cramped_string:
        ctypedef char value_type

        # these should really be allocator_type.size_type and
        # allocator_type.difference_type to be true to the C++ definition
        # but cython doesn't support deferred access on template arguments
        ctypedef size_t size_type
        ctypedef ptrdiff_t difference_type

        string(const string& s) except +

        void swap(cramped_string& other)

        bint operator==(const cramped_string&)

        bint operator!= (const cramped_string&)
