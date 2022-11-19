import collections.abc

try:
    from cstrstrdict import (
        CStrStrDict,
    )
except ImportError:
    raise RuntimeError('Unable to import strstrdict bindings.')


class StrStrDict(CStrStrDict, collections.abc.MutableMapping):
    """
    Low memory overhead alternative to Python's `dict`. Drop-in replacement.
    Only supports string keys and values. Data is not ordered.
    """
    def __init__(self,  *args, **attrs):
        super().__init__()
        self.update(*args, **attrs)
