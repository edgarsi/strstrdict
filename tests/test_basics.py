import pytest

from strstrdict import StrStrDict


def test_valid_commands_work():
    d = StrStrDict({'a': 'b'})
    assert len(d) == 1
    d['c'] = 'd'
    assert len(d) == 2
    d['c'] = 'dd'
    assert len(d) == 2
    d.update({'e': 'f'})
    assert len(d) == 3
    del d['a']
    assert len(d) == 2
    assert dict(d) == {'c': 'dd', 'e': 'f'}


def test_invalid_commands_fail():
    d = StrStrDict({'a': 'b'})
    with pytest.raises(KeyError):
        d['c']
    with pytest.raises(KeyError):
        del d['c']
    with pytest.raises(TypeError):
        d['c'] = 1
    with pytest.raises(TypeError):
        d.update({'c': 1})
    with pytest.raises(TypeError):
        d[1] = 'c'
    with pytest.raises(TypeError):
        d.update({1: 'c'})
    with pytest.raises(TypeError):
        d[1]
    with pytest.raises(TypeError):
        del d[1]
    with pytest.raises(TypeError):
        d[b'c'] = 'd'


def test_modifying_invalidates_iterators():
    d = StrStrDict({'a': 'b', 'c': 'd'})
    it = iter(d)
    next(it)
    d['e'] = 'f'
    with pytest.raises(RuntimeError):
        next(it)
    it = iter(d)
    next(it)
    d['a'] = 'a'
    with pytest.raises(RuntimeError):
        next(it)
    it = iter(d)
    next(it)
